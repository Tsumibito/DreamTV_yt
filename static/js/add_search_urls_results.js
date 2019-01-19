(function() {
    'use strict';

    $(document).ready(function($) {

        function postProcessing(data) {
            var myData = data;
            var my_tab = drawTable(myData)
            $('tbody').html(my_tab);
            setTimeout(getValues, 5000);
        }

        getValues();

        function getValues(){
            $.ajax({
                url: 'http://127.0.0.1:8000/generator/add_search_urls/processor/',
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
            var added = 0;
            var lost = 0;
            for (var i = 0; i < data.result.length; i++){
                var color_state = data.result[i].created === true? 'table success' : 'table danger';
                //console.log(data.result[i])
                html_code += '<tr class="' + color_state +'">';
                html_code += '<td>'+ (i+1) +'</td>';
                html_code += '<td><a target="_blank"' + data.result[i].url + '">' + data.result[i].url + '</a></td>';
                html_code += '<td>' + data.result[i].created + '</td>';
                if (data.result[i].created === true){
                    added +=1;
                }
                else {
                    lost += 1
                }
            }
            $('#work-fine').children().html(added)
            $('#junk').children().html(lost)
            return html_code
        }

    });
})()

