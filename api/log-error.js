/**
 * Vercel Serverless Function to receive error logs
 * POST /api/log-error
 */

export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const errorLog = req.body;

    // Log to Vercel's server logs (visible in Vercel dashboard)
    console.error('🚨 Client Error:', JSON.stringify(errorLog, null, 2));

    // You can also:
    // 1. Save to a database
    // 2. Send to an external service (Sentry, LogRocket, etc.)
    // 3. Send email notifications for critical errors
    // 4. Save to a file (if using Vercel's file system)

    // Example: Save to a simple log file (if using Vercel's file system)
    // Note: Vercel serverless functions are stateless, so you'd need
    // to use an external service for persistent storage

    return res.status(200).json({ 
      success: true, 
      message: 'Error logged successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error in log-error handler:', error);
    return res.status(500).json({ 
      error: 'Failed to log error',
      message: error.message 
    });
  }
}

