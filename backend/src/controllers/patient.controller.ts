import { Request, Response } from 'express';
import { aiService } from '../services/ai.service';

export const getPatients = async (req: Request, res: Response) => {
  try {
    const patients = await aiService.getPatients();
    res.json(patients);
  } catch (error) {
    console.error('Error in getPatients:', error);
    res.status(500).json({
      error: 'Failed to fetch patients',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};
