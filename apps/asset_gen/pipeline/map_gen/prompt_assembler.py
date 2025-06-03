from pipeline.map_gen.map_summarizer import summarize_map_folder

def assemble_prompt(user_description: str, reference_folder: str = "map_reference") -> str:
    """
    사용자의 자연어 요청과 참고용 맵 요약을 하나의 LLM 프롬프트로 조립한다.
    """
    reference_summary = summarize_map_folder(reference_folder)
    
    template = f"""
                당신은 플랫폼 점프 게임의 맵 설계 AI입니다.
                아래는 참고할 수 있는 기존 맵 구조 요약입니다:

                {reference_summary}

                ---

                사용자 요청:
                "{user_description}"

                요청에 맞는 맵을 section 단위로 나누고, 아래 JSON 형식으로만 응답해 주세요:

                [
                {{
                    "section_id": 1,
                    "type": "straight",      // "split", "merge", "jump", "spiral" 중 하나
                    "length": 10,
                    "direction": "x+",
                    "keyword": "연잎"
                }},
                ...
                ]
                """.strip()

    return template
