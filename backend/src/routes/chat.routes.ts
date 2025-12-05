import { Router } from 'express';
import { chat } from '../controllers/chat.controller';

const router = Router();

// POST /api/chat - Chat with patient file
router.post('/', chat);

export default router;
