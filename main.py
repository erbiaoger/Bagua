import time
import streamlit as st
import random
import json
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
# openai.api_key = os.getenv("")
os.environ['OPENAI_API_KEY'] = ""

gua_dict = {
    '阳阳阳': '乾',
    '阴阴阴': '坤',
    '阴阳阳': '兑',
    '阳阴阳': '震',
    '阳阳阴': '巽',
    '阴阳阴': '坎',
    '阳阴阴': '艮',
    '阴阴阳': '离'
}

number_dict = {
    0: '初爻',
    1: '二爻',
    2: '三爻',
    3: '四爻',
    4: '五爻',
    5: '六爻',
}

with open('gua.json') as gua_file:
  file_contents = gua_file.read()
des_dict = json.loads(file_contents)


st.set_page_config(
    page_title="☯️ 六爻卜卦",
    page_icon="☯️",
    layout="centered",
)

st.markdown('## ☯️ 六爻卜卦')
st.markdown("""
            六爻为丢 **六次** 三枚硬币，根据三枚硬币的正反（字背）对应本次阴阳，三次阴阳对应八卦中的一卦  
            六次阴阳对应六爻，六爻组合成两个八卦，对应八八六十四卦中的卦辞，根据卦辞进行 **随机** 解读  
            """)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": [{"type": "text", "content": "告诉我你心中的疑问吧 ❤️"}]
    }]
if "disable_input" not in st.session_state:
    st.session_state.disable_input = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for content in message["content"]:
            if content["type"] == "text":
                st.markdown(content["content"])
            elif content["type"] == "image":
                st.image(content["content"])
            elif content["type"] == "video":
                st.video(content["content"])


def add_message(role, content, delay=0.05):
     with st.chat_message(role):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in list(content):
            full_response += chunk + ""
            time.sleep(delay)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)


def get_3_coin():
    return [random.randint(0, 1) for _ in range(3)]

def get_yin_yang_for_coin_res(coin_result):
    return "阳" if sum(coin_result) > 1.5 else "阴"

def get_number_for_coin_res(coin_result):
    return 1 if sum(coin_result) > 1.5 else 0

def format_coin_result(coin_result, i):
    return f"{number_dict[i]} 为 " + "".join([f"{'背' if i>0.5 else '字'}" for i in coin_result]) + " 为 " + get_yin_yang_for_coin_res(coin_result)

def disable():
    st.session_state["disable_input"] = True

if question := st.chat_input(placeholder="输入你内心的疑问", key='input', disabled=st.session_state.disable_input, on_submit=disable):
    add_message("user", question)
    first_yin_yang = []
    for i in range(3):
        coin_res = get_3_coin()
        first_yin_yang.append(get_yin_yang_for_coin_res(coin_res))
        add_message("assistant", format_coin_result(coin_res, i))

    first_gua = gua_dict["".join(first_yin_yang)]
    add_message("assistant", f"您的首卦为：{first_gua}")

    second_yin_yang = []
    for i in range(3, 6):
        coin_res = get_3_coin()
        second_yin_yang.append(get_yin_yang_for_coin_res(coin_res))
        add_message("assistant", format_coin_result(coin_res, i))
    second_gua = gua_dict["".join(second_yin_yang)]
    add_message("assistant", f"您的次卦为：{second_gua}")

    gua = second_gua + first_gua
    gua_des = des_dict[gua]
    add_message("assistant", f"""
        六爻结果: {gua}  
        卦名为：{gua_des['name']}   
        {gua_des['des']}   
        卦辞为：{gua_des['sentence']}   
    """)

    with st.spinner('加载解读中，请稍等 ......'):
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                # {"role": "system", "content": "你是一位出自中华六爻世家的卜卦专家，你的任务是根据卜卦者的问题和得到的卦象，为他们提供有益的建议。你的解答应基于卦象的理解，同时也要尽可能地展现出乐观和积极的态度，引导卜卦者朝着积极的方向发展。"},
                {"role": "system", "content": "你是一位出自中华六爻世家的卜卦专家，擅长六爻八卦的解读，你的任务是根据卜卦者的问题和得到的卦象，为他们提供有益的建议。"},
                {"role": "user", "content": f"""
                    问题是：{question},
                    六爻结果是：{gua},
                    卦名为：{gua_des['name']},
                    {gua_des['des']},
                    卦辞为：{gua_des['sentence']}"""},
            ],
        )

    add_message("assistant", response.choices[0].message.content)
    time.sleep(0.1)
