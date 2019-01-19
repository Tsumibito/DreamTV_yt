(function() {
    'use strict';

    $(document).ready(function($) {

        function postProcessing(data) {
            var myData = data;
            var my_tab = drawTable(myData)
            $('tbody').html(my_tab);
            setTimeout(getValues, 10000);
        }

        getValues();

        function getValues(){
            $.ajax({
                url: 'http://127.0.0.1:8000/generator/check_urls/processor/',
                type: 'get',
                dataType: 'json',
                cache: false,
                success: postProcessing,
                async:true,
                error: function(){
                    alert('Data Error');
                    document.location.reload();
                }
            });
        };

        function drawTable(data) {
            var html_code = '';
            var work_fine = 0;
            var junk = 0;
            for (var i = 0; i < data.length; i++){
                var color_state = data[i].status === 'SUCCESS' && data[i].result !== 'True'
                    ? 'table danger' : data[i].status === 'SUCCESS' && data[i].result === 'True'
                    ? 'table success' : data[i].status === 'STARTED' ? 'table warning' : 'table active';
                html_code += '<tr class="' + color_state +'">';
                html_code += '<td>'+ (i+1) +'</td>';
                html_code += '<td><a target="_blank" href="' + data[i].test + '">' + data[i].url + '</a></td>';
                html_code += '<td>' + data[i].status + '</td>';
                html_code += '<td>' + data[i].result + '</td>';
                if (data[i].status === 'SUCCESS' && data[i].result === 'True'){
                    work_fine +=1;
                }
                else if (data[i].status === 'SUCCESS' && data[i].result === 'False'){
                    junk += 1
                }

            }
            $('#work-fine').children().html(work_fine)
            $('#junk').children().html(junk)
            return html_code
        }

    });
})()

