document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#book_isbn')) {
      // Initialize new request
      const request = new XMLHttpRequest();
      const isbn = document.querySelector('#book_isbn').innerText;
      console.log(isbn);

      url = 'http://127.0.0.1:5000'+'/api/' + isbn;

      console.log(url)

      request.open('GET', url);

      //Callback function for when request completes
      request.onload = () => {
        console.log(request.responseText);
        console.log(request.status);
        const data = JSON.parse(request.responseText);
        console.log(data.isbn)

        if (request.status === 200) {
          const goodReadBookJSON = JSON.parse(request.responseText);

          let book_goodread_li_averagescore = document.createElement('li');
          book_goodread_li_averagescore.className = "list-group-item";


          let textnode_goodread_averagescore = document.createTextNode("Average Score: " + goodReadBookJSON.averagescore);
          book_goodread_li_averagescore.appendChild(textnode_goodread_averagescore);

          let book_goodread_li_reviewcount = document.createElement('li');
          book_goodread_li_reviewcount.className = "list-group-item";

          let textnode_goodread_reviewcount = document.createTextNode("Review Count: " + goodReadBookJSON.reviewcount);
          book_goodread_li_reviewcount.appendChild(textnode_goodread_reviewcount);


          document.querySelector('#book_goodread_ul').appendChild(book_goodread_li_averagescore);
          document.querySelector('#book_goodread_ul').appendChild(book_goodread_li_reviewcount);

        }
        else {

          let book_goodread_li_error = document.createElement('li');
          book_goodread_li_error.className = "list-group-item";


          let textnode_goodread_error = document.createTextNode("Error: " + "No data available on Good Reads.");
          book_goodread_li_error.appendChild(textnode_goodread_error);

          document.querySelector('#book_goodread_ul').appendChild(book_goodread_li_error);

        }

      }


      //Send request
      request.send();

    }
});