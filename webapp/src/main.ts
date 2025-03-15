import "./css/style.css";
import "./css/normalize.css";
import Alpine from "alpinejs";
import { gameState } from "./ts/app";

window.Alpine = Alpine;
Alpine.data('gameState', gameState)
Alpine.start();

// const userId = "1";

// const response = await fetch("http://localhost:8000/stats?user_id=" + userId, {
// 	method: "GET",
// 	headers: {
// 		"ngrok-skip-browser-warning": "truuu",
// 	},
// });

// const data = await response.json();
// console.log(data);
