import json
import glob
import os

# 스크립트 실행 폴더에 생성된 json 확인
json_files = sorted(glob.glob(r"D:\jaehyuk.myung\claude_demo\Demo_13_QA\script_by_antigravity(gemini)\test_result_TC*.json"))
if not json_files:
    json_files = sorted(glob.glob(r"D:\jaehyuk.myung\claude_demo\Demo_13_QA\test_result_TC*.json"))

print("| 테스트 ID | 테스트명 | 점검 요소 | 필수 여부 | 요소 결과 |")
print("| :--- | :--- | :--- | :--- | :--- |")

for f in json_files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            test_id = os.path.basename(f).replace("test_result_", "").replace(".json", "")
            test_name = data.get("test_name", "")
            if ":" in test_name:
                test_name = test_name.split(":", 1)[1].strip()
            
            elements = data.get("element_checks", {})
            
            if not elements:
                print(f"| {test_id} | {test_name} | - | - | **{data.get('overall_result', '')}** |")
            else:
                for elem_name, check in elements.items():
                    req = "필수" if check.get("required") else "선택"
                    status = check.get("status", "FAIL")
                    print(f"| {test_id} | {test_name} | {elem_name} | {req} | **{status}** |")
    except Exception as e:
        print(f"| {os.path.basename(f)} | Error parsing JSON | - | - | FAIL |")
