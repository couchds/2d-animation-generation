import React, { useState } from 'react';

const examplePrompts = [
  {
    title: "Cute Slime",
    prompt: "A cute blue slime with big, round eyes and a happy expression. It has a slight transparency and a glossy surface. The slime is bouncing slightly, with small sparkles around it."
  },
  {
    title: "Pixel Knight",
    prompt: "A pixel art style knight in shining armor. The character has a silver helmet with a red plume, a blue cape, and a golden sword. The armor has intricate engravings and the character is in a battle-ready stance."
  },
  {
    title: "Magical Cat",
    prompt: "A mystical cat with purple fur and glowing green eyes. It has a star-shaped marking on its forehead and is surrounded by floating magical orbs. The cat is sitting elegantly with its tail wrapped around its paws."
  }
];

const SpriteGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/generate-sprite', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ prompt }),
      // });
      // const data = await response.json();
      // setGeneratedImage(data.imageUrl);
      
      // Temporary mock response
      setTimeout(() => {
        setGeneratedImage('https://via.placeholder.com/512x512');
        setIsLoading(false);
      }, 2000);
    } catch (error) {
      console.error('Error generating sprite:', error);
      setIsLoading(false);
    }
  };

  const handleExampleClick = (examplePrompt: string) => {
    setPrompt(examplePrompt);
  };

  return (
    <div className="container mt-8">
      <div className="card">
        <div className="card-header">
          <h1 className="text-3xl font-bold">Sprite Generator</h1>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="prompt" className="form-label">
                Describe your character
              </label>
              <p className="form-description">
                Be as detailed as possible in your description. Include details about colors, style, expression, and any special features.
              </p>
              
              <div className="mb-4 flex flex-wrap gap-2">
                {examplePrompts.map((example, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleExampleClick(example.prompt)}
                    className="example-prompt-btn"
                  >
                    {example.title}
                  </button>
                ))}
              </div>

              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="form-input"
                placeholder="Example: A cute blue slime with big, round eyes and a happy expression. It has a slight transparency and a glossy surface. The slime is bouncing slightly, with small sparkles around it."
                required
              />
            </div>
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading}
            >
              {isLoading ? 'Generating...' : 'Generate Sprite'}
            </button>
          </form>

          {isLoading && (
            <div className="flex items-center justify-center p-8 mt-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          )}

          {generatedImage && !isLoading && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold mb-4">Generated Sprite</h2>
              <div className="flex justify-center">
                <img
                  src={generatedImage}
                  alt="Generated sprite"
                  className="max-w-full h-auto rounded-lg"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SpriteGenerator; 