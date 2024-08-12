// Importing CSS files
import './src/css/background_icons.css';
import './src/css/blur_group.css';
import './src/css/fades.css';
import './src/css/marquee.css';
import './src/css/scroller.css';

// Import all scripts into a single object
import allScripts from './src/js'; 

// Log a message
console.log('Fun effects loaded!');

// Re-export the combined scripts object (optional)
export default allScripts;
