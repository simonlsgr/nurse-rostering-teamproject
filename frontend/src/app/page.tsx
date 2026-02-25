import Link from "next/link"

export default function Home() {
  
  
  
  return (
    // place the login form a bit 
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <h1 className="text-4xl font-bold mb-4">Welcome!</h1>
        <p className="text-lg mb-8">Please log in to continue</p>
        <div className="flex flex-col items-center bg-white p-8 rounded-lg shadow-md">
          <form className="flex flex-col items-center">
            <input
              type="text"
              placeholder="Username"
              className="border border-gray-300 rounded-md px-4 py-2 mb-4 w-64"
            />
            <input
              type="password"
              placeholder="Password"
              className="border border-gray-300 rounded-md px-4 py-2 mb-4 w-64"
            />
            <Link className="w-full" href="/projects">
              <button
                type="submit"
                className="bg-blue-500 text-white rounded-md px-4 py-2 w-full hover:bg-blue-600 transition-colors duration-300"
              >
                Log In
              </button>
            </Link>

          </form>

        </div>
        <div className="mt-40 text-sm text-gray-600">
        </div>
      </div>

  );
}
