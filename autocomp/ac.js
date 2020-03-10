
// Only after document loaded
$(function() {

    console.log('doc ready in autocomp')

    // Configure species autocomplete
    $('#ac_selector').select2({
//        console.log('Applying select2 to elements')
        minimumInputLength: 3,
        // https://github.com/harvesthq/chosen/issues/1081#issuecomment-15088027
        search_contains: true,
        ajax: {
//            url: 'http://localhost:5000/api/3/action/tag_autocomplete?',
            url: 'https://gis-hub.ca/api/3/action/tag_autocomplete?',
            delay: 250,
            type: "POST",
            // Use json data
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            data: function (params) {
                var querydata = {
                    vocabulary_id: 'weather',
                    query: params.term
                    // Removed from URL: vocabulary_id=weather
                }
                console.log(querydata)
                return JSON.stringify(querydata)

            },
            processResults: function (data) {
                console.log('Result: ')
                console.log(data)
                var res = data.result.map(function (vocab) {
                    console.log(vocab)
                    return {id: vocab, text: vocab};
                });
                return {
                    results: res
                }
            }
        },
    })

    // Add species to list when selected
    $('#species_selector').on('select2:select', function (e) {
        var data = e.params.data
        console.log(data)
        var sp = $('#species_selector').val()
        console.log('Adding ' +sp)
        addSpecies(data.id, data.text)
    })

    // Remove when X clicked
    $('#species_enabled').on('click', '.sp-remove', function(){
        var id = $(this).parent().attr('id')
        console.log('Removing ' +id)
        $( '#'+id ).remove()
    })

    // Get all the enabled species ids and save
    $('#saveSpeciesList').click(function() {
        var id_list = []
        $('.sp-id').each( function() {
            id_list.push($(this).attr('id'))
        })
        // Get current project
        var selectedItemId = $('#itemId').val()
        var data = {project_id: selectedItemId, id_list: id_list}
        console.log('Saving ' +id_list.length+ ' species for ' +selectedItemId)
        var result = $.post({
            url: backendHost + '/project_species',
            data: JSON.stringify(data),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
        })
        result.done(function( ){
            $('#saveSpeciesList').html('Saved')
            $('#saveSpeciesList').prop( 'disabled', true )
        })
    })
})
