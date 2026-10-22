import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.config import settings

class JavaRunner:
    """
    Executes compiled or source-level Java code with isolated test inputs.
    Parses Java stdout into structured output and records runtime metrics.
    """
    def __init__(self, java_home: Optional[str] = None):
        self.java_home = java_home or settings.java_home
        if self.java_home:
            j_bin = Path(self.java_home) / "bin" / ("java.exe" if os.name == "nt" else "java")
            if j_bin.exists():
                self.java_bin = str(j_bin)
            elif os.path.exists(f"{self.java_home}/bin/java"):
                self.java_bin = f"{self.java_home}/bin/java"
            else:
                self.java_bin = "java"
        else:
            self.java_bin = "java"

    def execute(self, project_dir: Path, class_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        target_source = project_dir / "src" / "main" / "java" / "com" / "migration" / f"{class_name}.java"
        if not target_source.exists():
            # Fallback to direct project directory
            target_source = project_dir / f"{class_name}.java"
            if not target_source.exists():
                return {
                    "status": "ERROR",
                    "error_type": "MISSING_SOURCE_FILE",
                    "message": f"Source file not found: {target_source}"
                }

        # Ensure class is compiled
        class_file = target_source.with_suffix(".class")
        if not class_file.exists():
            if self.java_home:
                jc_bin = Path(self.java_home) / "bin" / ("javac.exe" if os.name == "nt" else "javac")
                javac_bin = str(jc_bin) if jc_bin.exists() else "javac"
            else:
                javac_bin = "javac"
            subprocess.run([javac_bin, str(target_source)], capture_output=True, timeout=15)

        # Build execution arguments
        args = [f"{k}={v}" for k, v in input_data.items()]
        
        # Check package
        content = target_source.read_text(encoding="utf-8", errors="ignore")
        if "package com.migration;" in content:
            cp_dir = project_dir / "src" / "main" / "java"
            full_class = f"com.migration.{class_name}"
        else:
            cp_dir = target_source.parent
            full_class = class_name

        cmd = [self.java_bin, "-cp", str(cp_dir), full_class] + args

        start_time = time.time()
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(project_dir)
            )
            exec_time_ms = (time.time() - start_time) * 1000.0

            if res.returncode != 0:
                return {
                    "status": "ERROR",
                    "error_type": "RUNTIME_ERROR",
                    "stderr": res.stderr,
                    "stdout": res.stdout,
                    "execution_time_ms": exec_time_ms
                }

            stdout = res.stdout
            if "___RESULT_JSON___" in stdout:
                json_part = stdout.split("___RESULT_JSON___", 1)[1].strip()
                try:
                    data = json.loads(json_part)
                    data["execution_time_ms"] = exec_time_ms
                    return data
                except json.JSONDecodeError:
                    return {
                        "status": "ERROR",
                        "error_type": "OUTPUT_PARSE_ERROR",
                        "raw_output": json_part,
                        "execution_time_ms": exec_time_ms
                    }

            return {
                "status": "OK",
                "raw_stdout": stdout,
                "execution_time_ms": exec_time_ms
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "ERROR",
                "error_type": "TIMEOUT",
                "message": "Java execution timed out after 15 seconds."
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error_type": "EXECUTION_EXCEPTION",
                "message": str(e)
            }
