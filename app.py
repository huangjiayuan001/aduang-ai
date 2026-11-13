import streamlit as st
from openai import OpenAI
import pypdf # 新增：用来读取 PDF 的工具
import io # 新增：用来处理文件数据流
# 1. 网页基本设置（这俩必须放在最上面）
st.set_page_config(page_title="阿黄的 AI 客服", page_icon="🛵")
st.title("📂 骑手阿黄的智能文件问答助手")

# 2. 连接 AI (填你自己的 Key)
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"], 
    base_url="https://api.deepseek.com"
)

# 3. 左侧边栏：清空聊天按钮
if st.sidebar.button("🧹 清空当前聊天记录"):
    st.session_state.messages = [] # 清空记忆
    st.rerun() # 刷新页面

# 🚨 新增：定义一个自动清空的函数
def clear_chat():
    st.session_state.messages = []

# 新增：角色选择器（带有 on_change 魔法）
ai_role = st.sidebar.selectbox(
    "请选择 AI 的角色：",
    ["数据提取专家（吐 JSON）", "毒舌面试官（疯狂吐槽）", "短视频文案写手（爆款文案）"],
    on_change=clear_chat
)


# 4. 网页上传文件按钮
# 在主页面放一个清空按钮
if st.button("🧹 清空聊天记录"):
    st.session_state.messages = [] # 把记忆清空
    st.rerun() # 刷新页面
uploaded_file = st.file_uploader("请上传你的资料文件 (.txt 或 .pdf)", type=["txt", "pdf"])

# 5. 判断：如果没传文件，给个提示
if uploaded_file is None:
    st.info("👆 请先在上方上传一份你的 .txt 规则文件，AI 才能开始工作哦！")

# 6. 如果上传了文件，就开始工作！
if uploaded_file is not None:
        # 如果是 txt 文件，就用原来的方法
    if uploaded_file.name.endswith(".txt"):
        rules_content = uploaded_file.read().decode("utf-8")
    
    # 如果是 pdf 文件，就用 pypdf 把字抽出来
    elif uploaded_file.name.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        rules_content = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                rules_content += text + "\n"
    st.write(f"📝 成功读取到的文字长度是：{len(rules_content)} 个字")
      # 初始化记忆库
        # 根据用户的选择，赋予 AI 不同的“灵魂”
    if ai_role == "数据提取专家（吐 JSON）":
         prompt_text = f"你是一个数据提取专家。请阅读以下资料，提取出关于外卖扣款的信息。你必须严格输出一个 JSON 格式的数据，不要包含任何其他解释文字。JSON 的键必须是 'rule_name' 和 'penalty_amount'。如果资料中没有提及，就输出 'null'。\n\n资料：\n{rules_content}"
        
    elif ai_role == "毒舌面试官（疯狂吐槽）":
         prompt_text = f"你是一个极其严厉的互联网大厂技术总监。你正在面试一个零基础想转行 AI 开发的骑手。请根据以下他的项目资料，用非常毒舌、严厉的语气挑刺，指出他项目里的漏洞和不足，不要留情面。\n\n资料：\n{rules_content}"
        
    else:
         prompt_text = f"你是一个千万粉丝的短视频爆款文案写手。请阅读以下资料。如果用户让你总结资料，你就帮他简明扼要地总结；如果用户让你写抖音文案，你就根据资料写出 3 条极具情绪价值的文案。\n\n资料：\n{rules_content}"
            
    st.session_state.messages = [
            {"role": "system", "content": prompt_text}
        ]
        
    # 显示历史对话
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
  
    # 提问输入框
    if prompt := st.chat_input("输入你想问文档里的问题："):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 发送给 AI
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                stream=True
            )
            
            def generate_text():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            full_response = st.write_stream(generate_text())
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
