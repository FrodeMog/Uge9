import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import Toast from 'react-bootstrap/Toast';
import { Card, Button, Form, InputGroup, FormControl, DropdownButton, Dropdown, Row, Col } from 'react-bootstrap';

const Cereal = () => {
        const navigate = useNavigate();
        const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);
        const decodedToken = loggedInUser ? jwtDecode(loggedInUser) : null;
        const username = decodedToken ? decodedToken.sub : null;
        const [showToast, setShowToast] = useState(false); 
        const [toastMessage, setToastMessage] = useState('');
        const manufacturers = {
            'A': 'American Home Food Products',
            'G': 'General Mills',
            'K': 'Kelloggs',
            'N': 'Nabisco',
            'P': 'Post',
            'Q': 'Quaker Oats',
            'R': 'Ralston Purina'
          };
          
        const types = {
            'C': 'Cold',
            'H': 'Hot'
          };

        const comparison_descriptions = {
            'eq': '=',
            'gt': '>',
            'lt': '<',
            'gte': '>=',
            'lte': '<=',
            'ne': '!=',
        };
        const [cereal, setCereal] = useState([]);
        const [currentPage, setCurrentPage] = useState(1);
        const itemsPerPage = 10;
        const totalPages = Math.ceil(cereal.length / itemsPerPage);
        const [fetchedPages, setFetchedPages] = useState([]);
        const [filters, setFilters] = useState({});
        const [operator, setOperator] = useState(null);
        const [value, setValue] = useState('');

        const [caloriesOperator, setCaloriesOperator] = useState(null);
        const [caloriesValue, setCaloriesValue] = useState(null);
        const [sodiumOperator, setSodiumOperator] = useState(null);
        const [sodiumValue, setSodiumValue] = useState(null);
        const [idOperator, setIdOperator] = useState(null);
        const [idValue, setIdValue] = useState(null);
        const [nameOperator, setNameOperator] = useState(null);
        const [nameValue, setNameValue] = useState(null);
        const [mfrOperator, setMfrOperator] = useState(null);
        const [mfrValue, setMfrValue] = useState(null);
        const [typeOperator, setTypeOperator] = useState(null);
        const [typeValue, setTypeValue] = useState(null);
        const [proteinOperator, setProteinOperator] = useState(null);
        const [proteinValue, setProteinValue] = useState(null);
        const [fatOperator, setFatOperator] = useState(null);
        const [fatValue, setFatValue] = useState(null);
        const [fiberOperator, setFiberOperator] = useState(null);
        const [fiberValue, setFiberValue] = useState(null);
        const [carboOperator, setCarboOperator] = useState(null);
        const [carboValue, setCarboValue] = useState(null);
        const [sugarsOperator, setSugarsOperator] = useState(null);
        const [sugarsValue, setSugarsValue] = useState(null);
        const [potassOperator, setPotassOperator] = useState(null);
        const [potassValue, setPotassValue] = useState(null);
        const [vitaminsOperator, setVitaminsOperator] = useState(null);
        const [vitaminsValue, setVitaminsValue] = useState(null);
        const [shelfOperator, setShelfOperator] = useState(null);
        const [shelfValue, setShelfValue] = useState(null);
        const [weightOperator, setWeightOperator] = useState(null);
        const [weightValue, setWeightValue] = useState(null);
        const [cupsOperator, setCupsOperator] = useState(null);
        const [cupsValue, setCupsValue] = useState(null);
        const [ratingOperator, setRatingOperator] = useState(null);
        const [ratingValue, setRatingValue] = useState(null);
        const [selectedOperator, setSelectedOperator] = useState("Operator");

        const [order, setOrder] = useState('asc');

        const handlePageChange = (newPage) => {
            setCurrentPage(newPage);
        };
        const handleFilterChange = (field, value) => {
            setFilters(prevFilters => ({ ...prevFilters, [field]: value }));
        };
        const handleOperatorChange = (setOperator, operator) => {
            setOperator(operator);
        };
        
        const handleValueChange = (setValue, event) => {
            setValue(event.target.value);
        };
        const handleFilterSubmit = (event) => {
            event.preventDefault();
            const newFilters = {};
            if (caloriesOperator && caloriesValue) {
                newFilters.calories = [caloriesOperator, parseInt(caloriesValue)];
            }
            if (sodiumOperator && sodiumValue) {
                newFilters.sodium = [sodiumOperator, parseInt(sodiumValue)];
            }
            if (idOperator && idValue) {
                newFilters.id = [idOperator, parseInt(idValue)];
            }
            if (nameOperator && nameValue) {
                newFilters.name = [nameOperator, nameValue];
            }
            if (mfrOperator && mfrValue) {
                newFilters.mfr = [mfrOperator, mfrValue];
            }
            if (typeOperator && typeValue) {
                newFilters.type = [typeOperator, typeValue];
            }
            if (proteinOperator && proteinValue) {
                newFilters.protein = [proteinOperator, parseFloat(proteinValue)];
            }
            if (fatOperator && fatValue) {
                newFilters.fat = [fatOperator, parseFloat(fatValue)];
            }
            if (fiberOperator && fiberValue) {
                newFilters.fiber = [fiberOperator, parseFloat(fiberValue)];
            }
            if (carboOperator && carboValue) {
                newFilters.carbo = [carboOperator, parseFloat(carboValue)];
            }
            if (sugarsOperator && sugarsValue) {
                newFilters.sugars = [sugarsOperator, parseFloat(sugarsValue)];
            }
            if (potassOperator && potassValue) {
                newFilters.potass = [potassOperator, parseFloat(potassValue)];
            }
            if (vitaminsOperator && vitaminsValue) {
                newFilters.vitamins = [vitaminsOperator, parseFloat(vitaminsValue)];
            }
            if (shelfOperator && shelfValue) {
                newFilters.shelf = [shelfOperator, parseInt(shelfValue)];
            }
            if (weightOperator && weightValue) {
                newFilters.weight = [weightOperator, parseFloat(weightValue)];
            }
            if (cupsOperator && cupsValue) {
                newFilters.cups = [cupsOperator, parseFloat(cupsValue)];
            }
            if (ratingOperator && ratingValue) {
                newFilters.rating = [ratingOperator, parseFloat(ratingValue)];
            }
            setFilters(newFilters);
        };
        useEffect(() => {
            const fetchCereals = async () => {
                try {
                    let response;
                    if (Object.keys(filters).length > 0) {
                        const data = {
                            filters: filters,
                            order: order
                        };
                        response = await api.post('/cereals/filter', data);
                    } else {
                        response = await api.get('/cereals');
                    }
                    const cereals = response.data;
                    setCereal(cereals);
                } catch (error) {
                    console.error('Failed to fetch cereals:', error);
                    let errorMessage = 'Failed to fetch cereals.';
                    if (error.response?.data?.detail) {
                        errorMessage = typeof error.response.data.detail === 'object' 
                            ? JSON.stringify(error.response.data.detail)
                            : error.response.data.detail;
                    }
                    if (error.response && error.response.status === 404) {
                        setCereal([]);
                        errorMessage = "None found for filters";
                    }
                    setToastMessage(errorMessage);
                    setShowToast(true);
                }
            };
            fetchCereals();
        }, [filters, order]);

        useEffect(() => {
            const fetchPictures = async () => {
                const cerealsOnPage = cereal.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
                const cerealsWithPictures = await Promise.all(cerealsOnPage.map(async cereal => {
                    try {
                        const pictureResponse = await api.get(`/cereals/${cereal.id}/picture`, { params: { response_type: 'base64' } });
                        return { ...cereal, picture: `data:image/jpeg;base64,${pictureResponse.data.image}` };
                    } catch (error) {
                        if (error.response && error.response.status === 404) {
                            return cereal; // Return the cereal without the picture if a 404 error occurs
                        } else {
                            throw error; // Re-throw the error if it's not a 404 error
                        }
                    }
                }));
                setCereal(prevCereal => {
                    const newCereal = [...prevCereal];
                    newCereal.splice((currentPage - 1) * itemsPerPage, itemsPerPage, ...cerealsWithPictures);
                    return newCereal;
                });
                setFetchedPages(prevPages => [...prevPages, currentPage]);
            };
            if (cereal.length > 0 && !fetchedPages.includes(currentPage)) {
                fetchPictures();
            }
        }, [currentPage, cereal, fetchedPages]);


        return (
            <div>
                <Toast onClose={() => setShowToast(false)} show={showToast} delay={300} autohide className="position-fixed top-50 start-50 translate-middle">
                    <Toast.Header>
                        <strong className="me-auto">Error</strong>
                    </Toast.Header>
                    <Toast.Body>{toastMessage}</Toast.Body>
                </Toast>
                <Form onSubmit={handleFilterSubmit}>
                    <Row>
                    <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Calories"
                                    onChange={(event) => handleValueChange(setCaloriesValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[caloriesOperator]}
                                    id="input-group-dropdown-2"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setCaloriesOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Sodium"
                                    onChange={(event) => handleValueChange(setSodiumValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[sodiumOperator]}
                                    id="input-group-dropdown-3"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setSodiumOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="ID"
                                    onChange={(event) => handleValueChange(setIdValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[idOperator]}
                                    id="input-group-dropdown-4"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setIdOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Name"
                                    onChange={(event) => handleValueChange(setNameValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[nameOperator]}
                                    id="input-group-dropdown-5"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setNameOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Manufacturer"
                                    onChange={(event) => handleValueChange(setMfrValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[mfrOperator]}
                                    id="input-group-dropdown-6"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setMfrOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Type"
                                    onChange={(event) => handleValueChange(setTypeValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[typeOperator]}
                                    id="input-group-dropdown-7"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setTypeOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Protein"
                                    onChange={(event) => handleValueChange(setProteinValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[proteinOperator]}
                                    id="input-group-dropdown-8"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setProteinOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Fat"
                                    onChange={(event) => handleValueChange(setFatValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[fatOperator]}
                                    id="input-group-dropdown-9"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setFatOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Fiber"
                                    onChange={(event) => handleValueChange(setFiberValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[fiberOperator]}
                                    id="input-group-dropdown-10"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setFiberOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Carbo"
                                    onChange={(event) => handleValueChange(setCarboValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[carboOperator]}
                                    id="input-group-dropdown-11"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setCarboOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Sugars"
                                    onChange={(event) => handleValueChange(setSugarsValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[sugarsOperator]}
                                    id="input-group-dropdown-12"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setSugarsOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Potass"
                                    onChange={(event) => handleValueChange(setPotassValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[potassOperator]}
                                    id="input-group-dropdown-13"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setPotassOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Vitamins"
                                    onChange={(event) => handleValueChange(setVitaminsValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[vitaminsOperator]}
                                    id="input-group-dropdown-14"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setVitaminsOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Shelf"
                                    onChange={(event) => handleValueChange(setShelfValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[shelfOperator]}
                                    id="input-group-dropdown-15"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setShelfOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Weight"
                                    onChange={(event) => handleValueChange(setWeightValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[weightOperator]}
                                    id="input-group-dropdown-16"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setWeightOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Cups"
                                    onChange={(event) => handleValueChange(setCupsValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[cupsOperator]}
                                    id="input-group-dropdown-17"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setCupsOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                        <Col xs={1}>
                            <InputGroup>
                                <FormControl
                                    placeholder="Rating"
                                    onChange={(event) => handleValueChange(setRatingValue, event)}
                                />
                                <DropdownButton
                                    as={InputGroup.Append}
                                    variant="outline-secondary"
                                    title={comparison_descriptions[ratingOperator]}
                                    id="input-group-dropdown-18"
                                >
                                    {Object.entries(comparison_descriptions).map(([operator, description]) => (
                                        <Dropdown.Item key={operator} onClick={() => handleOperatorChange(setRatingOperator, operator)}>
                                            {description}
                                        </Dropdown.Item>
                                    ))}
                                </DropdownButton>
                            </InputGroup>
                        </Col>
                    </Row>
                    <Button type="submit">Apply Filters</Button>
                </Form>
                <div className="d-flex flex-wrap justify-content-around">
                    {cereal.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((cereal) => (
                        <Card style={{ width: '18rem' }} key={cereal.id}>
                            <Card.Img 
                                variant="top" 
                                src={cereal.picture || 'placeholder.jpg'} 
                                style={{ 
                                    width: '100%', 
                                    maxHeight: '100px', 
                                    height: 'auto', 
                                    objectFit: 'contain' 
                                }} 
                            />
                            <Card.Body>
                                <Card.Title>{cereal.id} - {cereal.name}</Card.Title>
                                <Card.Text>Manufacturer: {cereal.mfr} = {manufacturers[cereal.mfr]}</Card.Text>
                                <Card.Text>Type: {cereal.type} = {types[cereal.type]}</Card.Text>
                                <Card.Text>Calories: {cereal.calories}</Card.Text>
                                <Card.Text>Protein: {cereal.protein}</Card.Text>
                                <Card.Text>Fat: {cereal.fat}</Card.Text>
                                <Card.Text>Sodium: {cereal.sodium}</Card.Text>
                                <Card.Text>Fiber: {cereal.fiber}</Card.Text>
                                <Card.Text>Carbohydrates: {cereal.carbo}</Card.Text>
                                <Card.Text>Sugars: {cereal.sugars}</Card.Text>
                                <Card.Text>Potassium: {cereal.potass}</Card.Text>
                                <Card.Text>Vitamins: {cereal.vitamins}</Card.Text>
                                <Card.Text>Shelf: {cereal.shelf}</Card.Text>
                                <Card.Text>Weight: {cereal.weight}</Card.Text>
                                <Card.Text>Cups: {cereal.cups}</Card.Text>
                                <Card.Text>Rating: {cereal.rating}</Card.Text>
                            </Card.Body>
                        </Card>
                    ))}
            </div>
            <div className="d-flex justify-content-center">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <Button key={page} onClick={() => handlePageChange(page)} disabled={page === currentPage}>
                        {page}
                    </Button>
                ))}
            </div>
        </div>
    );
};

export default Cereal;