




//var sp_code_str
function load_sp_data(sp_data_str){
    console.log('Load codes: ' +sp_data_str)
    var sp_data = JSON.parse(sp_data_str)
    console.log(sp_data)
    /* Append each row using templates. Once loaded, set values using jQuery. */
    sp_data.forEach(function(item, i){

        var selectAgeData = `<select id="age_data${i}" class="age_data form-control">
            <option value="" selected></option>
            <option value="True">True</option>
            <option value="False">False</option>
            </select>`
        
        var selectObsType = `<select id="obs_type${i}" class="obs_type form-control">
            <option value="" selected></option>
            <option value="Targeted">Targeted observation</option>
            <option value="Incidental">Incidental observation</option>
            <option value="Inferred">Inferred</option>
            </select>`

        console.log(item)
        var tbl_row = `<tr id="species${i}">`
              + '<td>' +item.sp_code+ '</td>'
              + '<td>' +selectAgeData+ '</td>'
              + '<td>' +selectObsType+ '</td>'
              + '</tr>';
        console.log(tbl_row)
        $('#ac_js_table').append(tbl_row)
        // Set values in row
        console.log('Set age_data '+item.age_data)
        $('#age_data'+i).val(item.age_data)
        // $('#species'+i).find('.age_data').val(item.age_data)
        console.log('Set obs_type '+item.obs_type)
        $('#obs_type'+i).val(item.obs_type)
        // $('#species'+i).find('.obs_type').val(item.obs_type)
        // Bind the change detect event
        $('#age_data'+i).on('change', function(){
            speciesTableChanged()
        })
        $('#obs_type'+i).on('change', function(){
            speciesTableChanged()
        })
        $('#species'+i).find('.obs_type.age_data').on('change', function(){
            speciesTableChanged()
        })
    })
}

function speciesTableChanged (){
    console.log('Change in ac_js_table')
}




$(document).ready(function() {
    console.log('Activate species codes composite field on species_codes_js')
    // Get value from the text field itself
    // Enable this later once field is active, for now only test
    // var sp_data_str = $('#field-species_codes_js').val()
    var sp_data_str = "[{\"sp_code\": \"01C\", \"age_data\": \"False\", \"obs_type\": \"Inferred\"}]";

    load_sp_data(sp_data_str)
    // Activate change detection on table 
    $('#ac_js_table tr').on('.age_data.obs_type', 'change', function() {
        speciesTableChanged()
    })
})