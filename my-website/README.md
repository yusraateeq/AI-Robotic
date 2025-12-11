# AI-Humanaid Textbook Website

This is a Docusaurus-based textbook website for AI and Humanoid Robotics. It features the RAG chatbot integrated directly into the pages, allowing students to ask questions about the content.

## Features

- Interactive textbook content
- Built-in AI assistant (RAG chatbot)
- Text selection and context-aware queries
- Responsive design for all devices
- Modern, clean interface

## Installation

```bash
# Install dependencies
npm install

# Start the development server
npm run start
```

## Environment Variables

Create a `.env` file in this directory with:

```env
REACT_APP_API_URL=http://localhost:8000  # URL to your RAG backend API
```

## Running Locally

1. Make sure the RAG backend is running on port 8000
2. Run `npm run start` to start the Docusaurus server on port 3000
3. Visit `http://localhost:3000` to view the textbook

## Building for Production

```bash
npm run build
```

This will create a `build/` directory with the compiled static files.

## Key Components

- The `RagChatbot` component provides the AI assistant functionality
- The Root.js file ensures the chatbot is available on all pages
- Textbook content is in the `docs/` directory
- The chatbot automatically detects text selections

## Project Structure

- `src/pages/` - Main pages of the site
- `src/components/` - Reusable React components
- `docs/` - Textbook content in Markdown format
- `src/components/RagChatbot/` - AI assistant component