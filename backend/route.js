import Nylas from 'nylas';

const NylasConfig = {
  apiKey: process.env.NYLAS_API_KEY,
  apiUri: process.env.NYLAS_API_REGION_URI,
 };
 
 const nylas = new Nylas(NylasConfig);

const sendEmail = async (req, res) => {
  const user = res.locals.user;

  const { to, subject, body } = req.body;
  // TODO: Consider using replyToMessageId


  const sentMessage = await nylas.messages.send({
    identifier: user.grantId,
    requestBody: {
      to: [{ email: to }],
      replyTo: [{ email: user.emailAddress }],
      subject: subject,
      body: body
    },
  });

  return res.json(sentMessage);
};

const readEmails = async (req, res) => {
  const user = res.locals.user;

  console.log({user})

  const threads = await nylas.threads.list({
    identifier: user.grantId,
    queryParams: {
      limit: 5,
    }
  });
  
  return res.json(threads.data);
};

const getMessage = async (req, res) => {
  const user = res.locals.user;

  const { id: messageId } = req.query;
  
  const message = await nylas.messages.find({
    identifier: user.grantId,
    messageId,
  });

  return res.json(message.data);
};

const getMessages = async (req, res) => {
  const user = res.locals.user;

  const { id: threadId } = req.query;
  
  const messages = await nylas.messages.list({
    identifier: user.grantId,
    queryParams: {
      threadId,
    }
  });

  return res.json(messages.data);
};

const getFile = async (req, res) => {
  const user = res.locals.user;

  // TODO: Add messageId to req.query on the frontend
  const { id: attachmentId, messageId } = req.query;

  const attachment = await nylas.attachments.find({
    identifier: user.grantId,
    attachmentId,
    queryParams: { messageId }
  });
  
  return res.end(attachment);
};

const smartCompose = async (req, res) => {
  const user = res.locals.user;
  const { prompt } = req.body;

  try {
    const message = await nylas.messages.smartCompose.composeMessage({
      identifier: user.grantId,
      requestBody: {
        prompt: prompt,
      }
    });

    return res.json(message);
  } catch (error) {
    console.error('Smart Compose error:', error);
    return res.status(500).json({ error: 'Failed to generate message' });
  }
};

export default {
  sendEmail,
  readEmails,
  getMessage,
  getMessages,
  getFile,
  smartCompose,
}