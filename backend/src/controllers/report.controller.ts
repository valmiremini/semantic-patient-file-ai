import { Request, Response } from 'express';
import { aiService, ReportRequest } from '../services/ai.service';

export const generateReport = async (req: Request, res: Response) => {
  try {
    const { patient_id } = req.body;

    if (!patient_id) {
      return res.status(400).json({
        error: 'Missing required field',
        message: 'patient_id is required',
      });
    }

    const reportRequest: ReportRequest = {
      patient_id,
    };

    const response = await aiService.generateReport(reportRequest);
    res.json(response);
  } catch (error) {
    console.error('Error in generateReport:', error);
    res.status(500).json({
      error: 'Failed to generate report',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};
