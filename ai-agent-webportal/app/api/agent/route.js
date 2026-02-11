// Express server to ping the Flask server to send user input, and return the response 
import express from 'express';
import cors from "cors";

const app = express();
app.use(express.json());
app.use(cors({
  origin: "http://localhost:3000",
}));

app.post("/api/agent", async (req, res, next) => {
    try {
        const input = req.body.message;
        console.log("Received input");
        if (!input) {
            return res.status(404).send("No input provided");
        }

        const response = await fetch("http://localhost:8000/prompt", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: input }),
        });

        if(response.ok) {
            const data = await response.json();
            console.log(data);
            res.status(201).send(data);
        } else {
            res.status(response.status).send("Failed to get response from agent");
        }
        
    } catch (e) {
        console.error(e);
        res.status(500).send("Internal server error");
    }

});

app.listen(3001, () => {
    console.log("Server is running on port 3001");
})