setTimeout (function(){
        document.getElementById('submitButton').disabled = null;
        },20000);

        var countdownNum = 20;
        incTimer();

        function incTimer(){
        setTimeout (function(){
            if(countdownNum != 0){
            countdownNum--;
            document.getElementById('timeLeft').innerHTML = 'Кнопка активируется через ' + countdownNum + ' секунд.';
            incTimer();
            } else {
            document.getElementById('timeLeft').innerHTML = 'Готово!';
            }
        },1000);
        }