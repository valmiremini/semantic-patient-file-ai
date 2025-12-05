import { Router } from 'express';
import multer from 'multer';
import { uploadDocuments } from '../controllers/upload.controller';

const router = Router();

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['application/json', 'application/pdf', 'text/plain'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only JSON, PDF, and TXT files are allowed.'));
    }
  },
});

// POST /api/upload - Upload patient documents
router.post('/', upload.array('files', 10), uploadDocuments);

export default router;
