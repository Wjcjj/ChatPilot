def fill_prompt(template: str, variables: dict) -> str:
    """
    替换模板字符串中的 {key} 占位符。
    不会报 KeyError，缺少的 key 会原样保留。
    """
    result = template
    for key, value in variables.items():
        result = result.replace("{" + key + "}", str(value))
    return result
