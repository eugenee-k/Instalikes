$(document).ready(function() {
    $('#stats-form').submit(function(e) {
        e.preventDefault();
        $('#sync').prop("disabled", true);
        $('#sync').text("Backuping...");

        $.ajax({
            type: 'POST',
            url: '/stats',
            data: $('#stats-form').serialize(),

            success: function(data) {
                console.log(data);

                ReactDOM.render(
                    <span>{data.message}</span>,
                    document.querySelector("#message")
                );  

                if (data.message.includes('Instagram asks for a security code')) {
                    $('.code').removeClass( "hidden1" );
                }
                else {
                    $('.code').addClass( "hidden1" );

                    const TotalLiked = ({ dataa }) => (
                      <span>{`${dataa.likes.length} new likes, ${dataa.comments.length} new comments`}</span>
                    );

                    ReactDOM.render(
                        <TotalLiked dataa={data}/>, document.querySelector("#n_likes")
                    );  

                    if (data.likes.length) {
                        const LikesList = ({ likes }) => (
                            <React.Fragment>
                                {likes.map((dataa, index) => (
                                  <LikeItem key={index} index={index} dataa={dataa} totalLikes={likes.length} />
                                ))}
                            </React.Fragment>
                        );

                        const LikeItem = ({ index, dataa, totalLikes }) => (
                          <a href={`/details/${totalLikes - index}`}>
                            <img src={`data:image/jpeg;base64,${dataa.image[0]}`} class="img-thumbnail" alt={`Like ${index + 1}`} />
                          </a>
                        );

                        ReactDOM.render(
                            <LikesList likes={data.likes} />,
                            document.querySelector("#image-container1")
                        );      
                    }

                    if (data.comments.length) {
                        const CommentsList = ({ comments }) => (
                            <React.Fragment>
                                {comments.map((dataa, index) => (
                                  <CommentItem key={index} index={index} dataa={dataa} />
                                ))}
                            </React.Fragment>
                        );

                        const CommentItem = ({ index, dataa }) => {
                            const userName = dataa.comment.split('\n')[0].split(' ')[0];
                            const caption = dataa.comment.split('\n')[0].split(userName)[1];
                            const myUserName = dataa.comment.split('\n')[2].split(' ')[0];
                            const comment = dataa.comment.split('\n')[2].split(myUserName)[1]

                            return (
                                <div>
                                  <div class="wrapper">
                                    <b>{userName}</b>
                                    <span>{caption}</span>
                                  </div>
                                  <img src={`data:image/jpeg;base64,${dataa.image}`} class="img-thumbnail" alt={`Comm ${index + 1}`} />
                                  <br />
                                  <b class="mycomment">{myUserName}</b>
                                  <span>{comment}</span>
                                </div>
                            );
                        };

                        ReactDOM.render(
                            <CommentsList comments={data.comments} />,
                            document.querySelector("#image-container2")
                        ); 
                    }
                }

                $('#sync').text("Backup Likes");
                $('#sync').prop("disabled", false);
            },
            error: function(error) {
                console.log('Error:', error);
                $('#sync').text("Backup Likes");
                $('#sync').prop("disabled", false);
            }
        });
    });

    $('.comments').bind('scroll', scrBottom);
});

function scrBottom(e){
    var elem = $(e.currentTarget);

    if (elem[0].scrollHeight - elem.scrollTop() < elem.outerHeight() + 1) {
        var count = 0;
        var len = $('.comments div div').length;

        for (var i = 1; i <= len; i++){
            if ($('.comments div div:nth-child('+ i +')').hasClass("hidden")) {
                $('.comments div div:nth-child('+ i +')').removeClass("hidden");
                count++;
            }

            if (count == 10) {
                break;
            }
        }
    }
}
