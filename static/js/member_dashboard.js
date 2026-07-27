function markAttendance() {

    if (!navigator.geolocation) {
        alert("Geolocation is not supported.");
        return;
    }

    navigator.geolocation.getCurrentPosition(

        function (position) {

            let lat = position.coords.latitude;
            let lng = position.coords.longitude;

            fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`)
                .then(res => res.json())
                .then(data => {

                    let location = data.display_name;

                    window.location =
                        "/mark_attendance?lat=" + lat +
                        "&lng=" + lng +
                        "&location=" + encodeURIComponent(location);

                });

        },

        function () {

            alert("Location Permission Denied.");

        }

    );

}