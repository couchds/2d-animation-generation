import { Link } from 'react-router-dom';

export const Home = () => {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold mb-8">Welcome to 2D Animation Generator</h1>
      <p className="text-xl mb-8">
        Create beautiful 2D sprites and animations using AI
      </p>
      <div className="flex justify-center space-x-4">
        <Link
          to="/generate-sprite"
          className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600"
        >
          Generate Base Sprite
        </Link>
        <Link
          to="/generate-animation"
          className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600"
        >
          Generate Animation
        </Link>
      </div>
    </div>
  );
}; 