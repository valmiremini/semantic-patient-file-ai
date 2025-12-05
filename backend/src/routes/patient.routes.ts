import { Router } from 'express';
import { getPatients } from '../controllers/patient.controller';

const router = Router();

// GET /api/patients - Get all patients
router.get('/', getPatients);

export default router;
