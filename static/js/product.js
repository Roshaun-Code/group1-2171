document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.thumbs-up').forEach(button => {
      button.addEventListener('click', () => {
        alert('You liked this recommendation. We will show you more like it!');
      });
    });
  
    document.querySelectorAll('.thumbs-down').forEach(button => {
      button.addEventListener('click', () => {
        alert('You disliked this recommendation. We will try to improve our suggestions!');
      });
    });
  });
  