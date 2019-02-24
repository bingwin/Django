/**
 * Created by chengwenhao on 2017/9/7.
 */




module.exports = {
  *beforeSendRequest(requestDetail) {
    const localResponse = {
      statusCode: 200,
      header: { 'Content-Type': 'application/json' },
      body: ''
    };

    if (/\.(mp4|jpg|webp)/i.test(requestDetail.url)  ) {
      return {
        response: localResponse
      };
    }
  },
};