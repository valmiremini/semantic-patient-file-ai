import { Request, Response } from 'express';
import { aiService } from '../services/ai.service';

export const uploadDocuments = async (req: Request, res: Response) => {
  try {
    const { patient_id } = req.body;
    const files = req.files as Express.Multer.File[];

    if (!patient_id) {
      return res.status(400).json({
        error: 'Missing required field',
        message: 'patient_id is required',
      });
    }

    if (!files || files.length === 0) {
      return res.status(400).json({
        error: 'No files uploaded',
        message: 'At least one file is required',
      });
    }

    const response = await aiService.uploadDocuments(patient_id, files);
    res.json(response);
  } catch (error) {
    console.error('Error in uploadDocuments:', error);
    res.status(500).json({
      error: 'Failed to upload documents',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};
