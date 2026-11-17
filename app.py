from utils import extract_text_from_file
import streamlit as st
from openai import OpenAI
# 1. 网页基本设置（这俩必须放在最上面）
st.set_page_config(page_title="阿黄的 AI 客服", page_icon="🛵")
st.title("🏢 企业级智能文档解析助手")
st.caption("上传 PDF/TXT 文件，让 AI 帮你快速总结合同、提炼报告、解析制度。")

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
    # 第一道防线：拦截超大文件 (5MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("❌ 文件过大！为了防止服务器崩溃，请上传 5MB 以内的文件。")
        st.stop()  # 👈 加上这一句！强制终止程序，绝对不准往下跑
    else:
        # 第二道防线：异常捕获
        try:
            # 1. 读取文件
            rules_content = extract_text_from_file(uploaded_file)
            st.write(f"📝 成功读取到的文字长度是：{len(rules_content)} 个字")
            
            # 2. 初始化记忆库
            if "messages" not in st.session_state:
                if ai_role == "数据提取专家（吐 JSON）":
                    prompt_text = f"你是一个数据提取专家。请阅读以下资料，提取出关于外卖扣款的信息。你必须严格输出一个 JSON 格式的数据。\n\n资料：\n{rules_content}"
                elif ai_role == "毒舌面试官（疯狂吐槽）":
                    prompt_text = f"你是一个极其严厉的互联网大厂技术总监。请根据以下资料疯狂吐槽。\n\n资料：\n{rules_content}"
                else:
                    prompt_text = f"你是一个千万粉丝的短视频爆款文案写手。请根据以下资料写文案。\n\n资料：\n{rules_content}"
                    
                st.session_state.messages = [
                    {"role": "system", "content": prompt_text}
                ]
                
            # 3. 显示历史对话
            for msg in st.session_state.messages:
                if msg["role"] != "system":
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        
            # 4. 提问与流式输出
            if prompt := st.chat_input("输入你想问文档里的问题："):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

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

        except Exception as e:
            # 只要 try 里面任何地方报错，都会跳到这里
            st.error(f"❌ 解析失败：该文件可能已损坏或加密。错误信息：{e}")
            st.stop()
