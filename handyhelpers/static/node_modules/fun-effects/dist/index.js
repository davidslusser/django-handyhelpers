// Importing CSS files
import './dist/css/background_icons.min.css';
import './dist/css/blur_group.min.css';
import './dist/css/fades.min.css';
import './dist/css/marquee.min.css';
import './dist/css/scroller.min.css';

// Import all scripts into a single object
import allScripts from './src/js'; 

// Log a message
console.log('Fun effects loaded!');

// Re-export the combined scripts object (optional)
export default allScripts;
