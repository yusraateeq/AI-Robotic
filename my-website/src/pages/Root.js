import React from 'react';
import RagChatbot from '../components/RagChatbot';

// Root component that wraps the entire app
export default function Root({children}) {
  return (
    <>
      {children}
      <RagChatbot />
    </>
  );
}