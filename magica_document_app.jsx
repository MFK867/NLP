// Magica Document: App with Local Auth, GPT Formatting, and DOCX Export

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import TextStyle from '@tiptap/extension-text-style';
import Color from '@tiptap/extension-color';
import { saveAs } from 'file-saver';
import { Document, Packer, Paragraph } from "docx";

const users = [
  { email: "test@magica.com", password: "password123" },
];

export default function MagicaDocument() {
  const [prompt, setPrompt] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const editor = useEditor({
    extensions: [StarterKit, TextStyle, Color],
    content: '<h2>Hello from Magica Document</h2><p>Type here or use the AI prompt below.</p>'
  });

  const handlePromptSubmit = async () => {
    if (!editor || !prompt) return;

    const systemPrompt = `You are an AI document assistant. Based on the user instruction, modify or generate appropriate HTML content.`;
    const userInstruction = `Editor HTML: ${editor.getHTML()}\n\nInstruction: ${prompt}`;

    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer YOUR_OPENAI_API_KEY`
        },
        body: JSON.stringify({
          model: "gpt-4o",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userInstruction }
          ]
        })
      });

      const data = await response.json();
      const updatedHtml = data.choices?.[0]?.message?.content;

      if (updatedHtml && editor) {
        editor.commands.setContent(updatedHtml);
      }
    } catch (err) {
      console.error("Prompt failed", err);
    }

    setPrompt("");
  };

  const handleLogin = () => {
    const user = users.find(
      (u) => u.email === email && u.password === password
    );
    if (user) {
      setIsLoggedIn(true);
    } else {
      alert("Invalid credentials");
    }
  };

  const handleExport = () => {
    const html = editor.getHTML();
    const tempElement = document.createElement("div");
    tempElement.innerHTML = html;
    const text = tempElement.innerText;

    const doc = new Document({
      sections: [
        {
          properties: {},
          children: [
            new Paragraph(text)
          ]
        }
      ]
    });

    Packer.toBlob(doc).then(blob => {
      saveAs(blob, "magica_document.docx");
    });
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-white p-6 text-gray-800">
        <h1 className="text-3xl font-bold mb-6">Login to Magica Document</h1>
        <div className="max-w-md space-y-4">
          <Input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Button onClick={handleLogin}>Login</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6 text-gray-800">
      <h1 className="text-3xl font-bold mb-4">Magica Document</h1>

      <Card className="mb-4">
        <CardContent>
          <EditorContent editor={editor} className="prose max-w-full border p-4 rounded-md" />
        </CardContent>
      </Card>

      <div className="flex gap-2 mb-4">
        <Input
          placeholder="e.g., Make the heading bold"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <Button onClick={handlePromptSubmit}>Run Prompt</Button>
        <Button variant="outline" onClick={handleExport}>Export as DOCX</Button>
      </div>
    </div>
  );
}
