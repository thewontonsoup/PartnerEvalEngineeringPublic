import { Box, Button, Link } from "@mui/material";
import PvaLogo from "../images/PVA Logo.png";
import { useNavigate } from "react-router-dom";

export default function NavBar() {
  const navigate = useNavigate();

  return (
    <Box>
      <Button
        onClick={() => {
          navigate("/");
        }}
      >
        <img src={PvaLogo} alt="PVA Logo" className="pva-logo" />
      </Button>
    </Box>
  );
}
