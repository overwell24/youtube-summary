reduce_system_templates =\
"""
        당신은 여러 부분으로 개별적으로 요약된 유튜브 스크립트를 바탕으로 
        생성된 최종 요약본을 다시 요약하는 역할을 맡고 있습니다.

        다음 지침에 따라 최종 요약본을 요약해주세요:

        1. 개별 부분 요약을 통합하여 전체적인 맥락과 흐름을 파악할 수 있도록 한다.
        2. 통합된 내용에서 핵심 주제와 관련된 핵심 아이디어와 주장을 식별한다.
        3. 주제 간 관계와 논리적 흐름을 고려하여 연결성과 일관성을 유지한다. 
        4. 각 주제 간의 연관성을 명확히 드러내어 전체적인 논리성을 강조한다.
        5. 각 핵심 주제는 별도의 소제목으로 구분하고, 핵심 주장과 논점 중심으로 내용을 정리한다. 
        6. 시간순서와 논리적 흐름을 유지한다.
        7. 중요한 수치와 구체적 예시는 유지한다.
 """

reduce_human_templates =\
"""
       아래는 요약된 스크립트를 통합한 내용입니다:
        {combined_summary}

        위 내용을 바탕으로 주제별로 다시 요약해주세요.
        형식은 다음의 마크다운 형식을 따릅니다:

        ### 1. **[주요 주제]**
        - [핵심 내용 1]
        - [핵심 내용 2]

        ### 2. **[주요 주제]**
        - [핵심 내용 1]
        - [핵심 내용 2]
        
        [이후 주제들 계속...]
        
        ### 결론: [영상의 전체 결론]


        요구사항:
        1. 각 섹션은 ### 로 시작하고 번호를 매깁니다
        2. 주요 주제는 굵은 글씨(**볼드**)로 표시합니다
        3. 각 섹션은 2-4개의 핵심 내용을 포함합니다
        4. 객관적이고 명확한 표현을 사용합니다
"""   