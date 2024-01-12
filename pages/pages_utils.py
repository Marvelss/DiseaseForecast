# 带有全选的多选框
def multiselect_all(streamlit, value_list, label, temp_label_visibility):
    checkbox_all = streamlit.checkbox("全选")
    if checkbox_all:
        selected_options = streamlit.multiselect(
            label,
            value_list, value_list, label_visibility=temp_label_visibility)
    else:
        selected_options = streamlit.multiselect(
            label,
            value_list, label_visibility=temp_label_visibility)
    return selected_options


nodes1 = [
    {"label": "气象数据", "value": "气象数据"}
]
nodes2 = [{"label": "气象数据", "value": "气象数据", "children": [
    {"label": "温度", "value": "温度"},
]}]
