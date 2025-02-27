import Alpine from 'alpinejs'
import './css/style.css'
 
window.Alpine = Alpine
Alpine.start()

const userId = "1" 

const response = await fetch('http://localhost:8000/stats?user_id=' + userId,{
    method: 'GET',
    headers: {
        'ngrok-skip-browser-warning': 'truuu',
    },
})

const data = await response.json()
console.log(data)