import json
import glob
import os

json_files = sorted(glob.glob(r"D:\jaehyuk.myung\claude_demo\Demo_13_QA\test_result_TC*.json"))

with open(r"D:\jaehyuk.myung\claude_demo\Demo_13_QA\table.md", "w", encoding="utf-8") as out:
    out.write("| 테스트 ID | 테스트명 | 점검 요소 | 필수 여부 | 결과 |\n")
    out.write("| :--- | :--- | :--- | :--- | :--- |\n")
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
                    out.write(f"| {test_id} | {test_name} | (상세 요소 점검 사항 없음) | - | **{data.get('overall_result', '')}** |\n")
                else:
                    for elem_name, check in elements.items():
                        req = "필수" if check.get("required") else "선택"
                        status = check.get("status", "FAIL")
                        out.write(f"| {test_id} | {test_name} | {elem_name} | {req} | **{status}** |\n")
        except Exception as e:
            pass
