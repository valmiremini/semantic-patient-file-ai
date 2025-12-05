import { Router } from 'express';
import { generateReport } from '../controllers/report.controller';

const router = Router();

// POST /api/reports/generate - Generate discharge report
router.post('/generate', generateReport);

export default router;
