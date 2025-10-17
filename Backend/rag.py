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
    """Enhanced RAG system with better multi-file retrieval"""
    
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
                max_tokens=1500  # Increased for more comprehensive answers
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _initialize_prompt(self):
        """Initialize the prompt template with better instructions"""
        template = """You are an AI assistant that helps with supplier and company information. 
        Use the following context from multiple sources to provide a comprehensive answer.

        CONTEXT FROM VARIOUS SOURCES:
        {context}

        QUESTION: {question}

        INSTRUCTIONS:
        1. Synthesize information from ALL relevant sources
        2. If different sources have conflicting information, mention this
        3. Provide a comprehensive answer that considers all available data
        4. If you cannot find specific information, say so but still use what you have

        COMPREHENSIVE ANSWER:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def retrieve(self, question: str) -> Tuple[List[Document], List[str]]:
        """Retrieve relevant documents from ALL files with enhanced search"""
        try:
            # Use a larger k value to get more diverse results
            k = min(12, config.SIMILARITY_TOP_K * 2)  # Get more documents for better coverage
            
            documents = vector_store_manager.similarity_search(question, k=k)
            sources = list(set([doc.metadata.get('source', 'Unknown') for doc in documents]))
            
            logger.info(f"🔍 Retrieved {len(documents)} documents from {len(sources)} unique sources: {sources}")
            
            # If we have documents but from only one source, try to get more diversity
            if len(sources) == 1 and len(documents) > 3:
                logger.info("Only one source found, attempting to get more diverse results...")
                # Try with a different approach - get some random documents too
                try:
                    # Get a few random documents to increase diversity
                    all_docs = vector_store_manager.vector_store.get()
                    if all_docs and 'documents' in all_docs:
                        total_docs = len(all_docs['documents'])
                        if total_docs > len(documents):
                            # Add some random documents from other sources
                            import random
                            other_docs = []
                            for doc in all_docs['documents']:
                                doc_source = doc.metadata.get('source', 'Unknown') if hasattr(doc, 'metadata') else 'Unknown'
                                if doc_source not in sources:
                                    other_docs.append(doc)
                            
                            if other_docs:
                                # Add 2-3 random documents from other sources
                                random_samples = random.sample(other_docs, min(3, len(other_docs)))
                                documents.extend(random_samples)
                                sources = list(set([doc.metadata.get('source', 'Unknown') for doc in documents]))
                                logger.info(f"Added {len(random_samples)} random documents, now have {len(sources)} sources")
                except Exception as e:
                    logger.warning(f"Could not add diverse documents: {e}")
            
            return documents, sources
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return [], []
    
    def generate(self, question: str, context_docs: List[Document]) -> str:
        """Generate answer using context documents from multiple sources"""
        if not context_docs:
            return "I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing or ask about something else."
        
        try:
            # Organize context by source for better synthesis
            context_by_source = {}
            for doc in context_docs:
                source = doc.metadata.get('source', 'Unknown')
                if source not in context_by_source:
                    context_by_source[source] = []
                context_by_source[source].append(doc.page_content)
            
            # Build comprehensive context text
            context_sections = []
            for source, contents in context_by_source.items():
                source_content = "\n".join([f"- {content}" for content in contents[:3]])  # Limit per source
                context_sections.append(f"FROM {source}:\n{source_content}")
            
            context_text = "\n\n".join(context_sections)
            
            logger.info(f"📚 Using context from {len(context_by_source)} sources: {list(context_by_source.keys())}")
            
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
        """Main RAG pipeline with enhanced multi-source retrieval"""
        start_time = time.time()
        
        if not question or not question.strip():
            return {
                "answer": "Please provide a valid question.",
                "sources": [],
                "processing_time": 0.0
            }
        
        try:
            # Retrieve relevant documents from ALL sources
            context_docs, sources = self.retrieve(question)
            
            # Generate comprehensive answer
            answer = self.generate(question, context_docs)
            
            processing_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": sources,
                "processing_time": round(processing_time, 2),
                "documents_used": len(context_docs)
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            processing_time = time.time() - start_time
            return {
                "answer": "I'm sorry, but I encountered an unexpected error while processing your question.",
                "sources": [],
                "processing_time": round(processing_time, 2),
                "documents_used": 0
            }

# Global RAG system instance
rag_system = RAGSystem()

def answer_question(question: str) -> dict:
    """Public interface for answering questions"""
    return rag_system.answer_question(question)