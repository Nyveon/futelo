export function Telegram() {
	return {
		share(content: string) {
			window.location.href = `https://t.me/share/url?url=${encodeURIComponent(
				content
			)}`;
		},

		async getUserStats() {
			//todo: no more hardcoded userId and change backend URL
			let userId = 748207556; // new URLSearchParams(window.location.search).get('user_id');
			const apiUrl = "http://127.0.0.1:8000/stats?user_id=";

			if (!userId && window.Telegram.WebApp.initDataUnsafe.user) {
				userId = window.Telegram.WebApp.initDataUnsafe.user.id;
			}

			if (userId) {
				const response = await fetch(apiUrl + userId, {
					method: "GET",
					headers: {
						"ngrok-skip-browser-warning": "truuu",
					},
				});

				const data = await response.json();

				console.log(data);

				if (data.error) {
					console.error(data.error);
					return;
				}

				return {
					letterLimits: data.letter_limits_list,
					level: data.current_level,
					msgLeft: data.messages_next_level,
				};
			}
		},
	};
}
