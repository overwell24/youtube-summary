import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt_templates import stuff_templates, map_templates, reduce_templates
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableParallel
import tiktoken
from youtube_api import YouTubeAPI


class YouTubeSummary:
    def __init__(self, youtube_url, youtube_api):
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)   # GPT 모델 초기화
        self.max_tokens = 8192  # gpt-4o-mini max token
        self.youtube_url = youtube_url  
        self.youtube_api = youtube_api  # 의존성 주입 순환참조 해결

    def _split_text(self, text, chunk_size=3000, overlap=300):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        return text_splitter.split_text(text) 

    def _calculate_tokens(self, text):
        encoder = tiktoken.get_encoding("cl100k_base")
        tokens = encoder.encode(text)  
        return len(tokens)  
    
    def _create_stuff_chain(self):
        # 간단한 텍스트 처리 방식 (Stuff 방식)
        stuff_system_message = SystemMessagePromptTemplate.from_template(stuff_templates.stuff_system_templates)
        stuff_human_message = HumanMessagePromptTemplate.from_template(stuff_templates.stuff_human_templates)
        stuff_prompt = ChatPromptTemplate.from_messages([stuff_system_message, stuff_human_message])
        stuff_chain = stuff_prompt | self.llm | StrOutputParser()  
        return stuff_chain
    
    def _create_map_chain(self):
        # 텍스트를 분할하여 독립적으로 처리하는 방식 (Map 방식)
        map_system_message = SystemMessagePromptTemplate.from_template(map_templates.map_system_templates)
        map_human_message = HumanMessagePromptTemplate.from_template(map_templates.map_human_templates)
        map_prompt = ChatPromptTemplate.from_messages([map_system_message, map_human_message])
        map_chain = map_prompt | self.llm | StrOutputParser()  
        return map_chain

    def _create_reduce_chain(self):
        # 여러 부분을 결합하여 최종 결과를 만드는 방식 (Reduce 방식)
        reduce_system_message = SystemMessagePromptTemplate.from_template(reduce_templates.reduce_system_templates)
        reduce_human_message = HumanMessagePromptTemplate.from_template(reduce_templates.reduce_human_templates)
        reduce_prompt = ChatPromptTemplate.from_messages([reduce_system_message, reduce_human_message])
        reduce_chain = reduce_prompt | self.llm | StrOutputParser()  
        return reduce_chain
    
    def _summarize_long_youtube(self, subtitles):
        chunks = self._split_text(subtitles)  
        map_chain = self._create_map_chain()  
        inputs = [{"index": index+1, "chunk": chunk, "chunks_size": len(chunks)} for index, chunk in enumerate(chunks)]
        
        # map_chain을 딕셔너리로 래핑하여 RunnableParallel에 전달
        map_runnable = RunnableParallel(
            {
                "map_task": map_chain  # map_chain을 "map_task"라는 키로 딕셔너리에 전달
            }
        )
        summaries = map_runnable.batch(inputs)

        # 각 부분의 요약을 결합하여 최종 요약 생성
        reduce_chain = self._create_reduce_chain()
        combined_summary = "\n\n".join([f"영상의 {position + 1}번째 부분 요약: {summary}" for position, summary in enumerate(summaries)])
        final_summary = reduce_chain.invoke({"combined_summary": combined_summary})  
        return final_summary

    def _summarize_short_youtube(self, subtitles):
        stuff_chain = self._create_stuff_chain()
        summary = stuff_chain.invoke({"subtitles": subtitles})  
        return summary
    

    def summarize(self):
        
        subtitles = self.youtube_api.get_subtitles(self.youtube_url)  

        # 유튜브 자막  길이가 길이에 따라 다른 방식으로 요약 ( stuff, map&reduce )
        if self._calculate_tokens(subtitles) > self.max_tokens:
            summary = self._summarize_long_youtube(subtitles)  # 긴 영상 요약
            return summary
        else:
            summary = self._summarize_short_youtube(subtitles)  # 짧은 영상 요약
            return summary

