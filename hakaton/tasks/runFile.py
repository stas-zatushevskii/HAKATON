import subprocess

def compile_and_run_c_program(c_file_path, output_exec_name="program_exec", args=None):
    # Компиляция
    try:
        exec_path = f"../solutions/{output_exec_name}"
        subprocess.run(["gcc", c_file_path, "-o", exec_path], check=True)
        print(f"[OK] Компиляция прошла успешно: {c_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при компиляции: {e}")
        return {
            "success": False,
            "error": "Compilation failed",
            "stdout": "",
            "stderr": str(e)
        }

    # Подготовка команды с аргументами
    exec_path = f"../solutions/{output_exec_name}"
    cmd = [exec_path]
    if args:
        cmd.extend(map(str, args))  # преобразуем аргументы в строки

    # Запуск программы
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "success": True,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout.strip() if e.stdout else "",
            "stderr": e.stderr.strip() if e.stderr else "",
            "exit_code": e.returncode
        }

result = compile_and_run_c_program("../solutions/calc_args.c", output_exec_name="calc_args", args=[5, "+", 3])
print(result["stdout"])  # Ожидаем: 8.00