from langchain.text_splitter import RecursiveCharacterTextSplitter
import youtube_crawler as yt_crawler
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from concurrent.futures import ThreadPoolExecutor
import time

def split_text(text, chunk_size=3000, overlap=300):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    # 문자열 리스트 반환
    return text_splitter.split_text(text)  

def create_map_chain(llm):
    # 템플릿 생성
    map_system_message = SystemMessagePromptTemplate.from_template(
        """
        당신은 유튜브 스크립트를 요약하는 전문가입니다.
        
        다음의 지침을 따라 텍스트를 요약해주세요:
        1. 각 주제는 별도의 소제목으로 구분하고, 핵심 주장과 논점을 중심으로 내용을 정리합니다.
        2. 논리적 흐름을 유지하며, 반복되는 내용은 대표적인 예만 남깁니다.
        3. 불필요한 잡담이나 감정 표현은 제거합니다.
        4. 핵심 문제점과 제안된 해결책을 명확히 표현합니다.
        5. 중요한 수치와 구체적 예시는 유지한다.
        """
    )
    map_human_message = HumanMessagePromptTemplate.from_template(
        """
        다음의 텍스트를 주제별로 내용을 자세히 요약해주세요:
        텍스트: 
        {chunk}

        이 부분은 전체 스크립트의 {index}번째 부분이며, 총 {chunks_size}개의 부분으로 구성됩니다.
        """
    )

    # 프롬프트 생성
    map_prompt = ChatPromptTemplate.from_messages([map_system_message, map_human_message])
    #print(map_prompt.pretty_print())

    # chain 생성
    map_chain = map_prompt | llm | StrOutputParser()
    return map_chain

def create_reduce_chain(llm):
    # 시스템 메세지 생성
    reduce_system_message = SystemMessagePromptTemplate.from_template(
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
    )
    # 유저 메세지 생성
    reduce_human_message= HumanMessagePromptTemplate.from_template(
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
    )

    # prompt 생성
    reduce_prompt = ChatPromptTemplate.from_messages([reduce_system_message,reduce_human_message])
    #print(reduce_prompt.pretty_print())

    # chain 생성
    reduce_chain = reduce_prompt | llm | StrOutputParser()
    return reduce_chain


def get_summary_parallel(yt_link):
    start_time = time.time()

    subtitles = yt_crawler.get_subtitle(yt_link)
    chunks = split_text(subtitles)
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    map_chain = create_map_chain(llm)
    inputs = [{"index": index+1, "chunk": chunk, "chunks_size": len(chunks)} for index, chunk in enumerate(chunks)]
    print(f"자막 분할 시간: {time.time() - start_time:.2f}초")
    
    map_start = time.time()
    # 병렬 처리
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(map_chain.invoke, input) for input in inputs]
        summaries = [future.result() for future in futures]
    
    print(f"Map 단계 시간: {time.time() - map_start:.2f}초")
    reduce_start = time.time()

    reduce_chain = create_reduce_chain(llm)
    combined_summary = "\n\n".join([f"영상의 {position + 1}번째 부분 요약: {summary}" for position, summary in enumerate(summaries)])
    final_summary = reduce_chain.invoke({"combined_summary": combined_summary})
    print(f"Reduce 단계 시간: {time.time() - reduce_start:.2f}초")

    return final_summary


def get_summary(yt_link):
    start_time = time.time()
    subtitles = yt_crawler.get_subtitle(yt_link)
    chunks = split_text(subtitles)  # 문자열 리스트로 처리
    
    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4o-mini",
    )
    
    # map chain 생성
    map_chain = create_map_chain(llm)
    # 메세지 내용
    inputs = [{"index": index+1, "chunk": chunk, "chunks_size": len(chunks)} for index, chunk in enumerate(chunks)]
    print(f"자막 분할 시간: {time.time() - start_time:.2f}초")
    
    map_start = time.time()
    # inputs를 batch로 처리
    summaries = map_chain.batch(inputs)
    print(f"Map 단계 시간: {time.time() - map_start:.2f}초")

    reduce_start = time.time()

    # chain 생성
    reduce_chain = create_reduce_chain(llm)
    combined_summary = "\n\n".join([f"영상의 {position + 1}번째 부분 요약: {summary}" for position, summary in enumerate(summaries)])
    #print(combined_summary)
    final_summary = reduce_chain.invoke({#
        "combined_summary": combined_summary
    })
    print(f"Reduce 단계 시간: {time.time() - reduce_start:.2f}초")

    return final_summary


