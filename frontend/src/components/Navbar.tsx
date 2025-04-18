import { Link } from 'react-router-dom';

export const Navbar = () => {
  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold text-gray-800">
            2D Animation Generator
          </Link>
          <div className="flex space-x-4">
            <Link
              to="/generate-sprite"
              className="text-gray-600 hover:text-gray-900"
            >
              Generate Sprite
            </Link>
            <Link
              to="/generate-animation"
              className="text-gray-600 hover:text-gray-900"
            >
              Generate Animation
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}; 