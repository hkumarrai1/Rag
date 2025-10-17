import logging
import time
from typing import List, Tuple
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate

from config import config
from vectorstore import vector_store_manager

logger = logging.getLogger(__name__)

class RAGSystem:
    """Main RAG system handling retrieval and generation"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.prompt = self._initialize_prompt()
    
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize the language model"""
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=config.GEMINI_API_KEY,
                temperature=0.1,
                max_tokens=1000
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _initialize_prompt(self):
        """Initialize the prompt template"""
        template = """Use the following context to answer the question. 
        If you don't know the answer based on the context, say you don't know.

        Context:
        {context}

        Question: {question}

        Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def retrieve(self, question: str) -> Tuple[List[Document], List[str]]:
        """Retrieve relevant documents and extract sources"""
        try:
            documents = vector_store_manager.similarity_search(question)
            sources = list(set([doc.metadata.get('source', 'Unknown') for doc in documents]))
            return documents, sources
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return [], []
    
    def generate(self, question: str, context_docs: List[Document]) -> str:
        """Generate answer using context documents"""
        if not context_docs:
            return "I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing or ask about something else."
        
        try:
            context_text = "\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
                for doc in context_docs
            ])
            
            prompt_text = self.prompt.format(
                context=context_text,
                question=question
            )
            
            response = self.llm.invoke(prompt_text)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "I apologize, but I encountered an error while generating the answer. Please try again later."
    
    def answer_question(self, question: str) -> dict:
        """Main RAG pipeline with timing and error handling"""
        start_time = time.time()
        
        if not question or not question.strip():
            return {
                "answer": "Please provide a valid question.",
                "sources": [],
                "processing_time": 0.0
            }
        
        try:
            # Retrieve relevant documents
            context_docs, sources = self.retrieve(question)
            
            # Generate answer
            answer = self.generate(question, context_docs)
            
            processing_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": sources,
                "processing_time": round(processing_time, 2)
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            processing_time = time.time() - start_time
            return {
                "answer": "I'm sorry, but I encountered an unexpected error while processing your question.",
                "sources": [],
                "processing_time": round(processing_time, 2)
            }

# Global RAG system instance
rag_system = RAGSystem()

def answer_question(question: str) -> dict:
    """Public interface for answering questions"""
    return rag_system.answer_question(question)