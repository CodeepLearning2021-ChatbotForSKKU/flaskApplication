from flask import Flask, render_template, request
# flask web app framework를 사용하기 위함
from pyflowchart import Flowchart
# 플로우차트 시각화 모듈을 사용하기 위함
import json
# 데이터를 읽기 위함. 데이터베이스가 확장되어 mysql 등을 사용하게 된다면 수정 필요

from python2pseudo import l2pseudo
import pycode_similar
# 출처는 리드미에 명시됨. 각각 슈도코드 변환기, 코드 유사도 판독기 모듈
# 코드 유사도 판독기의 경우 필요에 따라 수정 필요

app = Flask(__name__)

# 루트 url을 받으면 home.html을 띄워줌
@app.route('/')
def render_home():
    return render_template("home.html")

# 코드 검증 POST request를 받을 때의 동작
@app.route("/request_answer", methods=["GET", "POST"])
def render_result():
    if request.method == "POST":
# 데이터 읽기
        with open('static/codes.json', 'r') as f:
            json_data = json.load(f)
        all_prof_answer_codes = json_data['codes']
        # print(all_prof_answer_codes)
        # print("form", request.form)
# 사용자가 home.html에 작성한 데이터 읽기
        question_id_select = request.form["question_id_select"]
        question_id = int(question_id_select)
        student_code = request.form["code_input_textarea"]
        # print(question_id, code_input)
# 유사도 계산
        try:
            prof_answer_codes = [c["codes"] for c in all_prof_answer_codes if (
                c["question_id"] == question_id)][0]
            # print(prof_answer_codes)
            # print(student_code)
            results = pycode_similar.detect([student_code] + prof_answer_codes)
            # print([results[x][1][0].plagiarism_percent for x in range(len(results))])
            min_sim = 1  # 가장 작은 유사도 값
            min_fun = None  # 가장 유사도가 적은 함수

            for x in range(len(results)):
                if min_sim >= results[x][1][0].plagiarism_percent:
                    min_sim = results[x][1][0].plagiarism_percent
                    min_fun = results[x][1][0].info_candidate.func_code
            # print(min_fun)
# 가장 작은 유사도를 지니는 함수의 유사도 값에 따라 다른 리워드 제공
            if min_sim > 0.7:  # 코드 공개
                return render_template("result_3.html", code=min_fun, question_info=f"Quiz {question_id_select}")
            elif min_sim > 0.3:  # 슈도 코드 공개
                return render_template("result_2.html", pseudocode=l2pseudo(min_fun), question_info=f"Quiz {question_id_select}")
            else:  # 플로우 차트 공개
                flowchart = Flowchart.from_code(min_fun)
                flowchart_code = flowchart.flowchart()
                return render_template("result_1.html", flowchart_code=flowchart_code, question_info=f"Quiz {question_id_select}")
# 사용자 코드에 문법 에러가 있을 경우 예외 화면을 띄움
        except SyntaxError as err:
            return render_template("result_exception.html", errmsg=err.msg, errtxt=err.text, question_info=f"Quiz {question_id_select}")


if __name__ == "__main__":
    app.run()
