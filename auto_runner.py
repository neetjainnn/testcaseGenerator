import time
import subprocess

def run_script():
    print("Running auto_testcase_generator.py")
    subprocess.run(["python", "auto_testcase_generator.py"])
    print("Run complete.\n")

if __name__ == "__main__":
    while True:
        run_script()
        print("Waiting 10 sec for next run...")
        time.sleep(10)
