import { Request, Response } from 'express';
import { aiService, ChatRequest } from '../services/ai.service';

export const chat = async (req: Request, res: Response) => {
  try {
    const { patient_id, question, conversation_history } = req.body;

    if (!patient_id || !question) {
      return res.status(400).json({
        error: 'Missing required fields',
        message: 'patient_id and question are required',
      });
    }

    const chatRequest: ChatRequest = {
      patient_id,
      question,
      conversation_history: conversation_history || [],
    };

    const response = await aiService.chat(chatRequest);
    res.json(response);
  } catch (error) {
    console.error('Error in chat:', error);
    res.status(500).json({
      error: 'Failed to process chat request',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};
