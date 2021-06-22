from flask import Flask, render_template, request
from pyflowchart import Flowchart
import json

from python2pseudo import l2pseudo
import pycode_similar

app = Flask(__name__)


@app.route('/')
def render_home():
    return render_template("home.html")


@app.route("/request_answer", methods=["GET", "POST"])
def render_result():
    if request.method == "POST":
        with open('static/codes.json', 'r') as f:
            json_data = json.load(f)
        all_prof_answer_codes = json_data['codes']
        # print(all_prof_answer_codes)
        # print("form", request.form)
        question_id_select = request.form["question_id_select"]
        question_id = int(question_id_select)
        student_code = request.form["code_input_textarea"]
        # print(question_id, code_input)

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

            if min_sim > 0.7:  # 코드 공개
                return render_template("result_3.html", code=min_fun, question_info=f"Quiz {question_id_select}")
            elif min_sim > 0.3:  # 슈도 코드 공개
                return render_template("result_2.html", pseudocode=l2pseudo(min_fun), question_info=f"Quiz {question_id_select}")
            else:  # 플로우 차트 공개
                flowchart = Flowchart.from_code(min_fun)
                flowchart_code = flowchart.flowchart()
                return render_template("result_1.html", flowchart_code=flowchart_code, question_info=f"Quiz {question_id_select}")

        except SyntaxError as err:
            return render_template("result_exception.html", errmsg=err.msg, errtxt=err.text, question_info=f"Quiz {question_id_select}")


if __name__ == "__main__":
    app.run()
