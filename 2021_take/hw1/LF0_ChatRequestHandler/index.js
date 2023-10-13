exports.handler = async (event) => {
    console.log(event);
    // TODO implement
    const response = {
        statusCode: 200,
        headers: {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        body: {
            data: {
                messages: [{
                    type: 'unstructured',
                    unstructured: {
                        text: "Chatbox under development..."
                    }
                }]
            }
        }
    };
    return response;
};
